#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string value) {
    std::vector<std::string> parts;
    size_t pos = 0;
    while (pos < value.length()) {
        size_t spacePos = value.find(' ', pos);
        parts.push_back(value.substr(pos, spacePos - pos));
        if (spacePos == std::string::npos) break;
        pos = spacePos + 1;
    }

    std::string result;
    for (const std::string& part : parts) {
        result += part;
    }

    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("coscifysu")) == ("coscifysu"));
}
