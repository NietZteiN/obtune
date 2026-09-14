#include<assert.h>
#include<bits/stdc++.h>
long f(std::string needle, std::string haystack) {
    int count = 0;
    while (haystack.find(needle) != std::string::npos) {
        haystack.replace(haystack.find(needle), needle.length(), "");
        count++;
    }
    return count;
}
int main() {
    auto candidate = f;
    assert(candidate(("a"), ("xxxaaxaaxx")) == (4));
}
