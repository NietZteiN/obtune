#include <assert.h>
#include <bits/stdc++.h>

long f(std::string text, std::string character) {
    return text.rfind(character);
}
int main() {
    auto candidate = f;
    assert(candidate(("breakfast"), ("e")) == (2));
}
