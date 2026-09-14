#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, std::string o) {
    if(s.find(o) == 0) {
        return s;
    }
    return o + f(s, o.substr(o.length() - 2, 1) + o.substr(0, o.length() - 2));
}
int main() {
    auto candidate = f;
    assert(candidate(("abba"), ("bab")) == ("bababba"));
}
