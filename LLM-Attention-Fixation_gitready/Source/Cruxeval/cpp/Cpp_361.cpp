#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    return std::count(text.begin(), text.begin() + text.find(':'), '#');
}
int main() {
    auto candidate = f;
    assert(candidate(("#! : #!")) == (1));
}
