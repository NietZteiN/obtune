#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text, std::string search) {
    std::transform(text.begin(), text.end(), text.begin(), ::tolower);
    std::transform(search.begin(), search.end(), search.begin(), ::tolower);
    return text.find(search);
}
int main() {
    auto candidate = f;
    assert(candidate(("car hat"), ("car")) == (0));
}
