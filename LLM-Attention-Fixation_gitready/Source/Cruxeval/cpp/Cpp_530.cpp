#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, std::string ch) {
    std::string sl = s;
    if (s.find(ch) != std::string::npos) {
        sl.erase(0, s.find_first_not_of(ch));
        if (sl.empty()) {
            sl += "!?";
        }
    } else {
        return "no";
    }
    return sl;
}
int main() {
    auto candidate = f;
    assert(candidate(("@@@ff"), ("@")) == ("ff"));
}
