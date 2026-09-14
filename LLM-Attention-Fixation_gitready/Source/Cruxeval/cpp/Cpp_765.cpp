#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    int count = 0;
    for (char c : text) {
        if (std::isdigit(c)) {
            count++;
        }
    }
    return count;
}
int main() {
    auto candidate = f;
    assert(candidate(("so456")) == (3));
}
