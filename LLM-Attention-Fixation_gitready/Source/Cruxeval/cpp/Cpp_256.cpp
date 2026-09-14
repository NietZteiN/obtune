#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text, std::string sub) {
    long a = 0;
    long b = text.length() - 1;

    while (a <= b) {
        long c = (a + b) / 2;
        if (text.rfind(sub, c) != std::string::npos && text.rfind(sub, c) >= c) {
            a = c + 1;
        } else {
            b = c - 1;
        }
    }

    return a;
}
int main() {
    auto candidate = f;
    assert(candidate(("dorfunctions"), ("2")) == (0));
}
