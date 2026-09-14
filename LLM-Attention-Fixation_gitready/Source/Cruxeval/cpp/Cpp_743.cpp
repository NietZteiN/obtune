#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    std::stringstream ss(text);
    std::string string_a, string_b;
    std::getline(ss, string_a, ',');
    std::getline(ss, string_b);
    
    return -(string_a.length() + string_b.length());
}
int main() {
    auto candidate = f;
    assert(candidate(("dog,cat")) == (-6));
}
