#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> array, long elem) {
    for(int i = 0; i < array.size(); i++) {
        if(array[i] == elem) {
            return i;
        }
    }
    return -1;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)6, (long)2, (long)7, (long)1})), (6)) == (0));
}
