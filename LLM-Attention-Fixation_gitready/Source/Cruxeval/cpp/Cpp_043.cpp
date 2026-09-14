#include<assert.h>
#include<bits/stdc++.h>
long f(std::string n) {
    for(char i : n) {
        if (!isdigit(i)) {
            n = "-1";
            break;
        }
    }
    return stoi(n);
}
int main() {
    auto candidate = f;
    assert(candidate(("6 ** 2")) == (-1));
}
