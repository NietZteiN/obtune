#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string strchar) {
    if (strchar.size() != 1) {
        throw std::invalid_argument("Char argument must be a single character string");
    }
    char char_ = strchar[0];
    std::vector<char> result(text.begin(), text.end());
    int index = text.rfind(char_);
    if (index != std::string::npos) {
        while (index > 0) {
            result[index] = result[index - 1];
            result[index - 1] = char_;
            index -= 2;
        }
    }
    return std::string(result.begin(), result.end());
}
int main() {
    auto candidate = f;
    assert(candidate(("qpfi jzm"), ("j")) == ("jqjfj zm"));
}
