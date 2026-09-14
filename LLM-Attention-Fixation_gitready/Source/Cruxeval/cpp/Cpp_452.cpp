#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    int counter = 0;
    for(char c : text) {
        if(std::isalpha(c)) {
            counter++;
        }
    }
    return counter;
}
int main() {
    auto candidate = f;
    assert(candidate(("l000*")) == (1));
}
