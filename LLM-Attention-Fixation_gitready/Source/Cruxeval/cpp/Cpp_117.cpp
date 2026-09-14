#include<assert.h>
#include<bits/stdc++.h>
long f(std::string numbers) {
    for(int i = 0; i < numbers.length(); i++) {
        if (std::count(numbers.begin(), numbers.end(), '3') > 1) {
            return i;
        }
    }
    return -1;
}
int main() {
    auto candidate = f;
    assert(candidate(("23157")) == (-1));
}
