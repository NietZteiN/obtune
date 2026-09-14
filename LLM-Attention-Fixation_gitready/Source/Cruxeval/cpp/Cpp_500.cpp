#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string delim) {
    std::string reversed = text;
    std::reverse(reversed.begin(), reversed.end());
    size_t pos = reversed.find(delim);
    if (pos != std::string::npos) {
        std::string result = reversed.substr(reversed.size() - pos);
        std::reverse(result.begin(), result.end());
        return result;
    }
    return "";
}
int main() {
    auto candidate = f;
    assert(candidate(("dsj osq wi w"), (" ")) == ("d"));
}
