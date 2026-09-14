#include<assert.h>
#include<bits/stdc++.h>
bool f(std::vector<long> mylist) {
    std::vector<long> revl = mylist;
    std::reverse(revl.begin(), revl.end());
    std::sort(mylist.begin(), mylist.end(), std::greater<long>());
    return mylist == revl;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)5, (long)8}))) == (true));
}
