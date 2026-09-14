#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, std::string x) {
    int count = 0;
    while (s.substr(0, x.length()) == x && count < s.length() - x.length()) {
        s = s.substr(x.length());
        count += x.length();
    }
    return s;
}
int main() {
    auto candidate = f;
    assert(candidate(("If you want to live a happy life! Daniel"), ("Daniel")) == ("If you want to live a happy life! Daniel"));
}
