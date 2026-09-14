#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    long n = 0;
    for (char i : text) {
        if (std::isupper(i)) {
            n += 1;
        }
    }
    return n;
}
int main() {
    auto candidate = f;
    assert(candidate(("AAAAAAAAAAAAAAAAAAAA")) == (20));
}
