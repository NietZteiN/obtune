#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, long n, std::string c) {
    long width = c.length() * n;
    while (s.length() < width) {
        s = c + s;
    }
    return s;
}
int main() {
    auto candidate = f;
    assert(candidate(("."), (0), ("99")) == ("."));
}
