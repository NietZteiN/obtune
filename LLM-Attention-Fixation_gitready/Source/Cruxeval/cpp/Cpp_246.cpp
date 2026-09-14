#include<assert.h>
#include<bits/stdc++.h>
long f(std::string haystack, std::string needle) {
    for (int i = static_cast<int>(haystack.find(needle)); i >= 0; --i) {
        if (haystack.substr(i) == needle) {
            return i;
        }
    }
    return -1;
}
int main() {
    auto candidate = f;
    assert(candidate(("345gerghjehg"), ("345")) == (-1));
}
