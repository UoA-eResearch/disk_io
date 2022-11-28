CREATE TABLE `fio_benchmarks` (
  `ts` timestamp NOT NULL,
  `facility` varchar(64) NOT NULL,
  `platform` varchar(32) NOT NULL,
  `config` varchar(256) NOT NULL,
  `bytes_ps_read` bigint NOT NULL,
  `iops_read` float NOT NULL,
  `bytes_ps_write` bigint NOT NULL,
  `iops_write` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='fio benchmarks';
