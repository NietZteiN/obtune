#include<assert.h>
#include<bits/stdc++.h>
long f(std::string sample) {
    long i = -1;
    while (sample.find('/', i+1) != std::string::npos) {
        i = sample.find('/', i+1);
    }
    std::string sub_str = sample.substr(0, i);
    for (long j = sub_str.size() - 1; j >= 0; --j) {
        if (sample[j] == '/') {
            return j;
        }
    }
    return -1;
}
int main() {
    auto candidate = f;
    assert(candidate(("present/here/car%2Fwe")) == (7));
}
