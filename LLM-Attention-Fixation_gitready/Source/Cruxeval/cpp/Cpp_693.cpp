#include<assert.h>
#include<bits/stdc++.h>

std::string f(std::string text) {
    size_t n = text.find('8');
    if (n == std::string::npos) {
        return "";
    }
    std::string result;
    for (size_t i = 0; i < n; ++i) {
        result += "x0";
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("sa832d83r xd 8g 26a81xdf")) == ("x0x0"));
}
