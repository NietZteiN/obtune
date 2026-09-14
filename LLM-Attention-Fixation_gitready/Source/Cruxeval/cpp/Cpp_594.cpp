#include<assert.h>
#include<bits/stdc++.h>
long f(std::string file) {
    return file.find('\n');
}
int main() {
    auto candidate = f;
    assert(candidate(("n wez szize lnson tilebi it 504n.\n")) == (33));
}
