#include<assert.h>
#include<bits/stdc++.h>
long f(std::string cat) {
    int digits = 0;
    for (char ch : cat) {
        if (isdigit(ch)) {
            digits++;
        }
    }
    return digits;
}
int main() {
    auto candidate = f;
    assert(candidate(("C24Bxxx982ab")) == (5));
}
