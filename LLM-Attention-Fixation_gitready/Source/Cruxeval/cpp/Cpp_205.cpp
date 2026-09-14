#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string a) {
    for (int i = 0; i < 10; i++) {
        for (int j = 0; j < a.length(); j++) {
            if (a[j] != '#') {
                a = a.substr(j);
                break;
            } else if (j == a.length() - 1) {
                a = "";
                break;
            }
        }
    }
    
    while (a.back() == '#') {
        a.pop_back();
    }
    
    return a;
}
int main() {
    auto candidate = f;
    assert(candidate(("##fiu##nk#he###wumun##")) == ("fiu##nk#he###wumun"));
}
