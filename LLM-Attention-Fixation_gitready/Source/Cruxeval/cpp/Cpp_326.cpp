#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    int number = 0;
    for (char t : text) {
        if (std::isdigit(t)) {
            number += 1;
        }
    }
    return number;
}
int main() {
    auto candidate = f;
    assert(candidate(("Thisisastring")) == (0));
}
