#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, std::string ch) {
    if(s.find(ch) == std::string::npos) {
        return "";
    }
    
    size_t index = s.find(ch);
    s = s.substr(index + 1);
    std::reverse(s.begin(), s.end());
    
    while(s.find(ch) != std::string::npos) {
        index = s.find(ch);
        s = s.substr(index + 1);
        std::reverse(s.begin(), s.end());
    }
    
    return s;
}
int main() {
    auto candidate = f;
    assert(candidate(("shivajimonto6"), ("6")) == (""));
}
