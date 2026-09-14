#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string input) {
    for(char c : input) {
        if(isupper(c)) {
            return false;
        }
    }
    return true;
}
int main() {
    auto candidate = f;
    assert(candidate(("a j c n x X k")) == (false));
}
