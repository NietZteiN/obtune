#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string chars) {
    std::string result = text;
    while (result.size() >= 6 && result.find(chars, result.size() - 3) != std::string::npos) {
        result.erase(result.size() - 3, 2);
    }
    while (!result.empty() && result.back() == '.') {
        result.pop_back();
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("ellod!p.nkyp.exa.bi.y.hain"), (".n.in.ha.y")) == ("ellod!p.nkyp.exa.bi.y.hain"));
}
