#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text, std::string suffix, long num) {
    std::string str_num = std::to_string(num);
    return text.substr(text.length() - suffix.length() - str_num.length()) == suffix + str_num;
}
int main() {
    auto candidate = f;
    assert(candidate(("friends and love"), ("and"), (3)) == (false));
}
