#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string value) {
    size_t pos = text.find(value);
    std::string left = text.substr(0, pos);
    std::string right = text.substr(pos + value.length());
    return right + left;
}
int main() {
    auto candidate = f;
    assert(candidate(("difkj rinpx"), ("k")) == ("j rinpxdif"));
}
