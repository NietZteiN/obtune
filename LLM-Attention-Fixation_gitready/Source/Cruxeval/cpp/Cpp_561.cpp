#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text, std::string digit) {
    int count = std::count(text.begin(), text.end(), digit[0]);
    return std::stoi(digit) * count;
}
int main() {
    auto candidate = f;
    assert(candidate(("7Ljnw4Lj"), ("7")) == (7));
}
