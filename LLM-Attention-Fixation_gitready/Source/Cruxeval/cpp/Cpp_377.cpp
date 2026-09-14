#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::stringstream ss;
    ss << text;
    std::string line;
    std::string result;

    while (std::getline(ss, line)) {
        if (!result.empty()) {
            result += ", ";
        }
        result += line;
    }

    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("BYE\nNO\nWAY")) == ("BYE, NO, WAY"));
}
