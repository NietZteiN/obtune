#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long n) {
    int length = text.length();
    return text.substr(length*(n%4), length);
}
int main() {
    auto candidate = f;
    assert(candidate(("abc"), (1)) == (""));
}
