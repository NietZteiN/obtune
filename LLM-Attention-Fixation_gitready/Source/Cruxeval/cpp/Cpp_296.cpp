#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string url) {
    size_t pos = url.find("http://www.");
    if (pos != std::string::npos) {
        return url.substr(pos + 11);
    }
    return url;
}
int main() {
    auto candidate = f;
    assert(candidate(("https://www.www.ekapusta.com/image/url")) == ("https://www.www.ekapusta.com/image/url"));
}
