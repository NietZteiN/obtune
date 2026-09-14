#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long num_digits) {
    long width = std::max(1L, num_digits);
    return std::string(width - text.length(), '0') + text;
}
int main() {
    auto candidate = f;
    assert(candidate(("19"), (5)) == ("00019"));
}
