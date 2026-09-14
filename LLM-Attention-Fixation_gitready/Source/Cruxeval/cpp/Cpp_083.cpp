#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string l = text.substr(0, text.find_last_of('0'));
    if (l.empty()) {
        return "-1:-1";
    }
    return std::to_string(l.length()) + ":" + std::to_string(l.find('0') + 1);
}
int main() {
    auto candidate = f;
    assert(candidate(("qq0tt")) == ("2:0"));
}
