#include<assert.h>
#include<bits/stdc++.h>
long f(std::string letters) {
    int count = 0;
    for(char l : letters) {
        if (std::isdigit(l)) {
            count += 1;
        }
    }
    return count;
}
int main() {
    auto candidate = f;
    assert(candidate(("dp ef1 gh2")) == (2));
}
