#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    long x = 0;
    if(std::all_of(text.begin(), text.end(), ::islower)) {
        for(char c : text) {
            if(std::isdigit(c) && c < '9') {
                x++;
            }
        }
    }
    return x;
}
int main() {
    auto candidate = f;
    assert(candidate(("591237865")) == (0));
}
