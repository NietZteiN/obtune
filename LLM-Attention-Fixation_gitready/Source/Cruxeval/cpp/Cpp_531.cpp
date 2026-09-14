#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string x) {
    if (text.find(x) != 0) {
        return f(text.substr(1), x);
    } else {
        return text;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("Ibaskdjgblw asdl "), ("djgblw")) == ("djgblw asdl "));
}
