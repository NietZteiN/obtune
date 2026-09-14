#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, std::string sep) {
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream tokenStream(s);
    
    while (std::getline(tokenStream, token, sep[0])) {
        tokens.push_back("*" + token);
    }

    std::reverse(tokens.begin(), tokens.end());

    return std::accumulate(tokens.begin(), tokens.end(), std::string{}, [](const std::string& a, const std::string& b) {
        return a + (a.empty() ? "" : ";") + b;
    });
}
int main() {
    auto candidate = f;
    assert(candidate(("volume"), ("l")) == ("*ume;*vo"));
}
