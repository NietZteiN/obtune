#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string delimiter) {
    size_t pos = text.rfind(delimiter);
    return text.substr(0, pos) + text.substr(pos + delimiter.length());
}
int main() {
    auto candidate = f;
    assert(candidate(("xxjarczx"), ("x")) == ("xxjarcz"));
}
