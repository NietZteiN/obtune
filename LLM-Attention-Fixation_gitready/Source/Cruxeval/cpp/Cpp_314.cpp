#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    if (text.find(',') != std::string::npos) {
        size_t pos = text.find(',');
        std::string before = text.substr(0, pos);
        std::string after = text.substr(pos + 1);
        return after + ' ' + before;
    }
    return std::string(",") + text.substr(text.find(' ') + 1) + " 0";
}
int main() {
    auto candidate = f;
    assert(candidate(("244, 105, -90")) == (" 105, -90 244"));
}
