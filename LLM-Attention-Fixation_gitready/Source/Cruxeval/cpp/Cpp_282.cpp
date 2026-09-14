#include<assert.h>
#include<bits/stdc++.h>
long f(std::string s1, std::string s2) {
    int position = 1;
    int count = 0;
    while (position > 0) {
        position = s1.find(s2, position);
        count += 1;
        position += 1;
    }
    return count;
}
int main() {
    auto candidate = f;
    assert(candidate(("xinyyexyxx"), ("xx")) == (2));
}
