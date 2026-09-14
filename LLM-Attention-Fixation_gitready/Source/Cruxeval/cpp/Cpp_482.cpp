#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string result = text;
    size_t pos = result.find("\\\"");
    while (pos != std::string::npos) {
        result.replace(pos, 2, "\"");
        pos = result.find("\\\"", pos + 1);
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("Because it intrigues them")) == ("Because it intrigues them"));
}
