package com.puck.finance;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;
import java.util.*;
interface Users extends JpaRepository<User,Long> { Optional<User> findByEmail(String email); }
interface Sessions extends JpaRepository<Session,Long> { Optional<Session> findByTokenHash(String hash); }
interface Entries extends JpaRepository<Entry,Long> { List<Entry> findByUserId(Long id); Optional<Entry> findByIdAndUserId(Long id,Long userId); }
