#include<assert.h>
#include<bits/stdc++.h>
long f(std::string string) {
    int upper = 0;
    for (char c : string) {
        if (std::isupper(c)) {
            upper++;
        }
    }
    return upper * ((upper % 2 == 0) ? 2 : 1);
}
int main() {
    auto candidate = f;
    assert(candidate(("PoIOarTvpoead")) == (8));
}
