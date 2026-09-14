#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    int count = 0;
    for(char i : text) {
        if(i == '.' || i == '?' || i == '!' || i == ',' || i == '.') {
            count++;
        }
    }
    return count;
}
int main() {
    auto candidate = f;
    assert(candidate(("bwiajegrwjd??djoda,?")) == (4));
}
