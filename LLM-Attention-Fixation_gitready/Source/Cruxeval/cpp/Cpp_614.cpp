#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text, std::string substr, long occ) {
    long n = 0;
    while (true) {
        size_t i = text.rfind(substr);
        if (i == std::string::npos) {
            break;
        } else if (n == occ) {
            return static_cast<long>(i);
        } else {
            n++;
            text = text.substr(0, i);
        }
    }
    return -1;
}
int main() {
    auto candidate = f;
    assert(candidate(("zjegiymjc"), ("j"), (2)) == (-1));
}
