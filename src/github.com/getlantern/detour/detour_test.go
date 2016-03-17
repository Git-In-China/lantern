package detour

import (
	"io/ioutil"
	"net"
	"net/http"
	"net/url"
	"testing"
	"time"

	"github.com/getlantern/testify/assert"
)

var (
	directMsg string = "hello direct"
	detourMsg string = "hello detour"
	iranResp  string = `HTTP/1.1 403 Forbidden
Connection:close

<html><head><meta http-equiv="Content-Type" content="text/html; charset=windows-1256"><title>M1-6
</title></head><body><iframe src="http://10.10.34.34?type=Invalid Site&policy=MainPolicy " style="width: 100%; height: 100%" scrolling="no" marginwidth="0" marginheight="0" frameborder="0" vspace="0" hspace="0"></iframe></body></html>Connection closed by foreign host.`
)

func TestBlockedImmediately(t *testing.T) {
	defer stopMockServers()
	proxiedURL, _ := newMockServer(detourMsg)
	DelayBeforeDetour = 20 * time.Millisecond
	mockURL, mock := newMockServer(directMsg)

	client := &http.Client{Timeout: 50 * time.Millisecond}
	mock.Timeout(200*time.Millisecond, directMsg)
	resp, err := client.Get(mockURL)
	assert.Error(t, err, "direct access to a timeout url should fail")

	log.Trace("Test dialing times out")
	client = newClient(proxiedURL, 50*time.Millisecond)
	resp, err = client.Get("http://255.0.0.1") // it's reserved for future use so will always time out
	if assert.NoError(t, err, "should have no error if dialing times out") {
		assertContent(t, resp, detourMsg, "should detour if dialing times out")
		time.Sleep(50 * time.Millisecond)
		assert.True(t, wlTemporarily("255.0.0.1:80"), "should be added to whitelist if dialing times out")
	}

	log.Trace("Test dialing refused")
	client = newClient(proxiedURL, 50*time.Millisecond)
	resp, err = client.Get("http://127.0.0.1:4325") // hopefully this port didn't open, so connection will be refused
	if assert.NoError(t, err, "should have no error if connection is refused") {
		assertContent(t, resp, detourMsg, "should detour if connection is refused")
		time.Sleep(50 * time.Millisecond)
		assert.True(t, wlTemporarily("127.0.0.1:4325"), "should be added to whitelist if connection is refused")
	}

	log.Trace("Test reading times out")
	u, _ := url.Parse(mockURL)
	resp, err = client.Get(mockURL)
	if assert.NoError(t, err, "should have no error if reading times out") {
		assertContent(t, resp, detourMsg, "should detour if reading times out")
		time.Sleep(50 * time.Millisecond)
		assert.True(t, wlTemporarily(u.Host), "should be added to whitelist if reading times out")
	}

	log.Trace("Test nonidempotent method")
	client = newClient(proxiedURL, 50*time.Millisecond)
	RemoveFromWl(u.Host)
	resp, err = client.PostForm(mockURL, url.Values{"key": []string{"value"}})
	if assert.Error(t, err, "Non-idempotent method should not be detoured in same connection") {
		assert.True(t, wlTemporarily(u.Host), "but should be added to whitelist so will detour next time")
	}
}

func TestBlockedAfterwards(t *testing.T) {
	defer stopMockServers()
	proxiedURL, _ := newMockServer(detourMsg)
	DelayBeforeDetour = 20 * time.Millisecond
	mockURL, mock := newMockServer(directMsg)
	client := newClient(proxiedURL, 50*time.Millisecond)

	log.Trace("Test directly accessible")
	mock.Msg(directMsg)
	u, _ := url.Parse(mockURL)
	resp, err := client.Get(mockURL)
	if assert.NoError(t, err, "should have no error if the host is directly accessible") {
		assertContent(t, resp, directMsg, "should access directly to directly accessible host")
		assert.False(t, whitelisted(u.Host), "directly accessible host should not be added to whitelist")
	}

	log.Trace("Test reading times out for a previously worked url")
	mock.Timeout(200*time.Millisecond, directMsg)
	resp, err = client.Get(mockURL)
	if assert.NoError(t, err, "but should have no error for the second time") {
		u, _ := url.Parse(mockURL)
		assertContent(t, resp, detourMsg, "should detour if reading times out")
		time.Sleep(50 * time.Millisecond)
		assert.True(t, wlTemporarily(u.Host), "should be added to whitelist if reading times out")
	}
}

func TestRemoveFromWhitelist(t *testing.T) {
	defer stopMockServers()
	proxiedURL, proxy := newMockServer(detourMsg)
	proxy.Timeout(200*time.Millisecond, detourMsg)
	mockURL, _ := newMockServer(directMsg)
	u, _ := url.Parse(mockURL)
	AddToWl(u.Host, false)

	log.Trace("Test removing an undetourable address out of whitelist")
	client := newClient(proxiedURL, 50*time.Millisecond)
	_, err := client.Get(mockURL)
	if assert.Error(t, err, "should have error if reading times out through detour") {
		assert.False(t, whitelisted(u.Host), "should be removed from whitelist if reading times out through detour")
	}

}

func TestClosing(t *testing.T) {
	defer stopMockServers()
	proxiedURL, proxy := newMockServer(detourMsg)
	proxy.Timeout(200*time.Millisecond, detourMsg)
	DelayBeforeDetour = 20 * time.Millisecond
	mockURL, mock := newMockServer(directMsg)
	mock.Msg(directMsg)
	DirectAddrCh = make(chan string)
	{
		if _, err := newClient(proxiedURL, 50*time.Millisecond).Get(mockURL); err != nil {
			log.Debugf("Unable to send GET request to mock URL: %v", err)
		}
	}
	u, _ := url.Parse(mockURL)
	addr := <-DirectAddrCh
	assert.Equal(t, u.Host, addr, "should get notified when a direct connetion has no error while closing")
}

func TestIranRules(t *testing.T) {
	defer stopMockServers()
	proxiedURL, _ := newMockServer(detourMsg)
	DelayBeforeDetour = 20 * time.Millisecond
	SetCountry("IR")
	mockURL, mock := newMockServer(directMsg)
	u, _ := url.Parse(mockURL)
	client := newClient(proxiedURL, 50*time.Millisecond)

	mock.Raw(iranResp)
	resp, err := client.Get(mockURL)
	if assert.NoError(t, err, "should not error if content hijacked in Iran") {
		assertContent(t, resp, detourMsg, "should detour if content hijacked in Iran")
		time.Sleep(50 * time.Millisecond)
		assert.True(t, wlTemporarily(u.Host), "should be added to whitelist if content hijacked")
	}

	// this test can verifies dns hijack detection if runs inside Iran,
	// but only will time out and detour if runs outside Iran
	resp, err = client.Get("http://" + iranRedirectAddr)
	if assert.NoError(t, err, "should not error if dns hijacked in Iran") {
		assertContent(t, resp, detourMsg, "should detour if dns hijacked in Iran")
		assert.True(t, wlTemporarily(u.Host), "should be added to whitelist if dns hijacked")
	}
}

func proxyTo(proxiedURL string) func(network, addr string) (net.Conn, error) {
	return func(network, addr string) (net.Conn, error) {
		u, _ := url.Parse(proxiedURL)
		log.Tracef("Using proxy at %s to dial addr %s", u.Host, addr)
		return net.Dial("tcp", u.Host)
	}
}

func newClient(proxyURL string, timeout time.Duration) *http.Client {
	return &http.Client{
		Transport: &http.Transport{
			Dial:              Dialer(proxyTo(proxyURL)),
			DisableKeepAlives: true,
		},
		Timeout: timeout,
	}
}
func assertContent(t *testing.T, resp *http.Response, msg string, reason string) {
	b, err := ioutil.ReadAll(resp.Body)
	assert.NoError(t, err, reason)
	assert.Equal(t, msg, string(b), reason)
	resp.Body.Close()
}
