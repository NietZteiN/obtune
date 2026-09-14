#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text) {
    bool b = true;
    for(char x : text) {
        if(isdigit(x)) {
            b = true;
        } else {
            b = false;
            break;
        }
    }
    return b;
}
int main() {
    auto candidate = f;
    assert(candidate(("-1-3")) == (false));
}
